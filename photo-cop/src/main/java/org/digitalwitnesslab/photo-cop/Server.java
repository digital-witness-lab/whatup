package org.digitalwitnesslab.photocop;

import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import com.google.protobuf.ByteString;
import org.digitalwitnesslab.photocop.PhotoCopGrpc;
import org.digitalwitnesslab.photocop.CheckPhotoRequest;
import org.digitalwitnesslab.photocop.CheckPhotoResponse;
import org.digitalwitnesslab.photocop.GetPhotoHashRequest;
import org.digitalwitnesslab.photocop.GetPhotoHashResponse;

import java.awt.image.*;
import java.io.*;
import javax.imageio.ImageIO;
import PhotoDNA.*;

public class Server {
    private io.grpc.Server server;

    private void start() throws IOException {
        int port = 50051;
        server = ServerBuilder.forPort(port)
                .addService(new PhotoCopImpl())
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
        server.start();
        server.blockUntilShutdown();
    }

    static class PhotoCopImpl extends PhotoCopGrpc.PhotoCopImplBase {
        @Override
        public void getPhotoHash(GetPhotoHashRequest request, StreamObserver<GetPhotoHashResponse> responseObserver) {

            byte[] hash;
            try {
                hash = generateHash(request.getPhoto().toByteArray());
            } catch (java.io.IOException e) {
                throw new RuntimeException("Could not generate hash from photo", e);
            }

            GetPhotoHashResponse response = GetPhotoHashResponse.newBuilder()
                    .setHash(ByteString.copyFrom(hash))
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }

        @Override
        public void checkPhoto(CheckPhotoRequest request, StreamObserver<CheckPhotoResponse> responseObserver) {

            byte[] hash;
            try {
                hash = generateHash(request.getPhoto().toByteArray());
            } catch (java.io.IOException e) {
                throw new RuntimeException("Could not generate hash from photo", e);
            }

            boolean isMatch = false;
            Map<String, String> matchDetails = new HashMap<>();

            CheckPhotoResponse.Builder response = CheckPhotoResponse.newBuilder()
                    .setIsMatch(isMatch)
                    .putAllMatchDetails(matchDetails);

            if (request.getGetHash()) {
                response.setHash(ByteString.copyFrom(hash));
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
