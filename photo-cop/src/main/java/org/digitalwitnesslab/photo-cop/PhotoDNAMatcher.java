package org.digitalwitnesslab.photocop;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.entity.mime.content.ByteArrayBody;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import org.digitalwitnesslab.photocop.PhotoCopDecision;
import org.digitalwitnesslab.photocop.MatchInfo;

import java.util.concurrent.ExecutionException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;

public class PhotoDNAMatcher {

    private final String photoDnaKey;
    private ObjectMapper objectMapper;
    private RateLimitRunner rateLimitExecutor;

    public PhotoDNAMatcher(String photoDnaKey) {
        this.photoDnaKey = photoDnaKey;
        this.objectMapper = new ObjectMapper();
        this.rateLimitExecutor = new RateLimitRunner(2048, 5, 1000);
    }

    public static void main(String[] args) {
        String photoDnaKey = System.getenv("PHOTO_DNA_KEY");
        if (photoDnaKey == null) {
            System.err.println("PHOTO_DNA_KEY environment variable is not set.");
            return;
        }

        // Example byte array representing image data (in real usage, this should be filled with actual image bytes)
        byte[] imageHash = {}; // Replace with actual image byte data

        PhotoDNAMatcher matcher = new PhotoDNAMatcher(photoDnaKey);

        try {
            Map<String, Object> response = matcher.match(imageHash);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public Map<String, Object> match_ratelimit(byte[] imageHash, byte[] cacheKey, int priority) throws IOException {
        try {
            return this.rateLimitExecutor.submit(() -> {
                return this.match(imageHash);
            }, cacheKey, priority).get();
        } catch (ExecutionException | InterruptedException e) {
            e.printStackTrace();
            return Map.of();
        }
    }

    public Map<String, Object> match(byte[] imageHash) throws IOException {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpPost uploadFile = new HttpPost("https://api.microsoftmoderator.com/photodna/v1.0/MatchEdgeHash");

            // Set up the multipart entity
            MultipartEntityBuilder builder = MultipartEntityBuilder.create();
            builder.addPart("edgeHashFile1", new ByteArrayBody(imageHash, "edgeHashFile1"));

            HttpEntity multipart = builder.build();
            uploadFile.setEntity(multipart);

            // Set headers
            uploadFile.setHeader("Ocp-Apim-Subscription-Key", photoDnaKey);

            // Execute request
            try (CloseableHttpResponse response = httpClient.execute(uploadFile)) {
                HttpEntity responseEntity = response.getEntity();
                if (responseEntity != null) {
                    String responseBody = EntityUtils.toString(responseEntity);
                    JsonNode jsonNode = objectMapper.readTree(responseBody);
                    Map<String, Object> responseJson = objectMapper.convertValue(jsonNode, Map.class);
                    return extractResult(responseJson);
                }
                return Map.of(); // Return an empty map if there's no response entity
            }
        }
    }

    static private Map<String, Object> extractResult(Map<String, Object> response) {
        Map<String, Object> result = new HashMap<>();
        Object matchResults = response.get("MatchResults");
        if (matchResults instanceof List<?>) {
            List<?> resultsList = (List<?>) matchResults;
            if (!resultsList.isEmpty()) {
                Object firstResult = resultsList.get(0);
                if (firstResult instanceof Map<?, ?>) {
                    return (Map<String, Object>) firstResult;
                }
            }
        }
        return result;
    }

    static public PhotoCopDecision.Builder resultsToProto(Map<String, Object> match) {
        PhotoCopDecision.Builder result = PhotoCopDecision.newBuilder();
        if (match == null || match.isEmpty()) {
            return result;
        }

        boolean isMatch = (boolean) match.get("IsMatch");
        result.setIsMatch(isMatch);
        if (!isMatch) {
            return result;
        }

        Object matchFlags = ((Map<String, Object>) match.get("MatchDetails")).get("MatchFlags");
        if (matchFlags instanceof List<?>) {
            List<Map<String, Object>> matchFlatsList = (List<Map<String, Object>>) matchFlags;
            List<MatchInfo> matchInfos = new ArrayList();
            for(Map<String, Object> element: matchFlatsList) {
                matchInfos.add(
                    MatchInfo.newBuilder()
                        .setSource((String) element.get("Source"))
                        .setDistance((int) element.get("MatchDistance"))
                        .addAllViolations((List<String>) element.get("Violations"))
                        .build()
                );
            }
            result.addAllMatches(matchInfos);
        }

        return result;
    }
}
