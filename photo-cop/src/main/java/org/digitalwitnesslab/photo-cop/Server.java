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
import java.io.*;
import javax.imageio.ImageIO;
import PhotoDNA.*;

public class Server {
    private io.grpc.Server server;

    private void start() throws IOException {
        start(50051);
    }

    private void start(int port) throws IOException {
        String photoDnaKey = System.getenv("PHOTO_DNA_KEY");

        server = ServerBuilder.forPort(port)
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
            try {
                hash = generateHash(request.getPhoto().toByteArray());
            } catch (java.io.IOException e) {
                throw new RuntimeException("Could not generate hash from photo", e);
            }

            Map<String, Object> match;
            try {
                match = photoDNAMatcher.match(hash);
            } catch (IOException e) {
                throw new RuntimeException("Could not get PhotoDNA match result", e);
            }

            PhotoCopDecision.Builder response = photoDNAMatcher.resultsToProto(match);

            if (request.getGetHash()) {
                PhotoCopHash pcHash = PhotoCopHash.newBuilder()
                        .setValue(ByteString.copyFrom(hash))
                        .build();
                response.setHash(pcHash);
            }

            responseObserver.onNext(response.build());
            responseObserver.onCompleted();
        }
    }

    private static byte[] generateHash(byte[] image) throws java.io.IOException {
		BufferedImage imgBuffer = null;
        ByteArrayInputStream bais = new ByteArrayInputStream(image);
		imgBuffer = ImageIO.read(bais);

	    PDNAClientHashResult preHashObject = PDNAClientHashGenerator.generatePreHash(imgBuffer);
	    byte[] preHash = preHashObject.generateBinaryPreHash();
        return preHash;
    }
}
