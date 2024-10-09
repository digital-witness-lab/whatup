package org.digitalwitnesslab.photocop;

import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import com.google.protobuf.ByteString;
import org.digitalwitnesslab.photocop.PhotoCopGrpc;
import org.digitalwitnesslab.photocop.CheckPhotoRequest;
import org.digitalwitnesslab.photocop.PhotoCopDecision;
import org.digitalwitnesslab.photocop.GetPhotoHashRequest;
import org.digitalwitnesslab.photocop.PhotoCopHash;

import java.awt.image.BufferedImage;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.io.*;
import javax.imageio.ImageIO;
import PhotoDNA.*;


public class Server {
    private io.grpc.Server server;

    private void start() throws IOException {
        String portStr = System.getenv("PHOTOCOP_PORT");
        int port;
        try {
           port = Integer.parseInt(portStr);
        }
        catch (NumberFormatException e) {
           port = 3447;
        }
        start(port);
    }

    private File loadTLSFile(String envvar) {
        String tlsPath = System.getenv(envvar);

        if (tlsPath == null || tlsPath.isEmpty()) {
            throw new IllegalArgumentException(envvar + " environment variable is not set or is empty.");
        }

        File tlsFile = new File(tlsPath);
        if (!tlsFile.exists()) {
            throw new IllegalArgumentException("TLS file does not exist: " + tlsPath);
        }
        return tlsFile;
    }

    private void start(int port) throws IOException, IllegalArgumentException {
        File tlsCertFile = loadTLSFile("PHOTOCOP_TLS_CERT");
        File tlsKeyFile = loadTLSFile("PHOTOCOP_TLS_KEY");
        String photoDnaKey = System.getenv("PHOTO_DNA_KEY");

        server = ServerBuilder.forPort(port)
                .useTransportSecurity(tlsCertFile, tlsKeyFile)
                .addService(new PhotoCopImpl(photoDnaKey))
                .build()
                .start();
        System.out.println("Server started, listening on " + port);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.err.println("*** shutting down gRPC server since JVM is shutting down");
            Server.this.stop();
            System.err.println("*** server shut down");
        }));
    }

    private void stop() {
        if (server != null) {
            server.shutdown();
        }
    }

    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        final Server server = new Server();
        // TODO: take in port from args
        server.start();
        server.blockUntilShutdown();
    }

    static class PhotoCopImpl extends PhotoCopGrpc.PhotoCopImplBase {
        PhotoDNAMatcher photoDNAMatcher;

        public PhotoCopImpl(String photoDnaKey) {
            this.photoDNAMatcher = new PhotoDNAMatcher(photoDnaKey);
        }

        @Override
        public void getPhotoHash(GetPhotoHashRequest request, StreamObserver<PhotoCopHash> responseObserver) {

            byte[] hash;
            try {
                hash = generateHash(request.getPhoto().toByteArray());
            } catch (java.io.IOException e) {
                throw new RuntimeException("Could not generate hash from photo", e);
            }

            PhotoCopHash response = PhotoCopHash.newBuilder()
                    .setValue(ByteString.copyFrom(hash))
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }

        @Override
        public void checkPhoto(CheckPhotoRequest request, StreamObserver<PhotoCopDecision> responseObserver) {

            byte[] hash;
            byte[] photo = request.getPhoto().toByteArray();

            try {
                hash = generateHash(photo);
            } catch (java.io.IOException e) {
                System.out.println("Could not generate hash from photo: " + e.getMessage());
                throw new RuntimeException("Could not generate hash from photo", e);
            }

            MessageDigest digest;
            try {
                digest = MessageDigest.getInstance("SHA-256");
            } catch(NoSuchAlgorithmException e) {
                System.out.println("Current java implemintation doesn't have sha-256: " + e.getMessage());
                throw new RuntimeException("Current java implemintation doesn't have sha-256.");
            }
            byte[] cacheKey = digest.digest(photo);
            int priority = request.getPriority();
            Map<String, Object> match;
            try {
                match = photoDNAMatcher.match_ratelimit(hash, cacheKey, priority);
            } catch (IOException e) {
                System.out.println("Could not get PhotoDNA match result: " + e.getMessage());
                throw new RuntimeException("Could not get PhotoDNA match result", e);
            }

            PhotoCopDecision.Builder responseBuilder = photoDNAMatcher.resultsToProto(match);

            if (request.getGetHash()) {
                PhotoCopHash pcHash = PhotoCopHash.newBuilder()
                        .setValue(ByteString.copyFrom(hash))
                        .build();
                responseBuilder.setHash(pcHash);
            }

            PhotoCopDecision response = responseBuilder.build();
            responseObserver.onNext(response);
            responseObserver.onCompleted();
            System.out.printf("Decision made: %s: %b\n", hash.toString(), response.getIsMatch());
        }
    }

    private static byte[] generateHash(byte[] image) throws java.io.IOException {
        ByteArrayInputStream bais = new ByteArrayInputStream(image);
		BufferedImage imgBuffer = ImageIO.read(bais);

        try {
	        PDNAClientHashResult preHashObject = PDNAClientHashGenerator.generatePreHash(imgBuffer);
	        byte[] preHash = preHashObject.generateBinaryPreHash();
            return preHash;
        } catch (java.lang.NullPointerException e) {
            System.out.println("Returning empty hash: " + e.getMessage());
            return new byte[0];
        }
    }
}
