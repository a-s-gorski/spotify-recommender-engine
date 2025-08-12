package com.example.authbackend.services;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.List;
import java.util.Map;

@Service
public class RecommendationService {
    
    @Value("${authbackend.api.url}")
    private String recommendationApiUrl;

    @Value("${authbackend.api.apikey}")
    private String apiKey;
    
    private final RestTemplate restTemplate;
    
    public RecommendationService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    /**
     * Get clustering-based recommendations
     */
    public List<String> getClusteringRecommendations(String playlistName, int k, int nNeighbors) {
        try {
            String url = UriComponentsBuilder.fromHttpUrl(recommendationApiUrl + "/recommend/recommend-clustering")
                    .queryParam("playlist_name", playlistName)
                    .queryParam("k", k)
                    .queryParam("n_neighbors", nNeighbors)
                    .toUriString();

            HttpHeaders headers = createHeaders();
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<List<String>> response = restTemplate.exchange(
                url, HttpMethod.GET, entity, new ParameterizedTypeReference<List<String>>() {}
            );

            return response.getBody();

        } catch (HttpClientErrorException e) {
            handleHttpError(e, "clustering recommendations");
            throw new RuntimeException("Failed to get clustering recommendations");
        }
    }
    
    /**
     * Get collaborative filtering recommendations
     */
    public List<String> getCollaborativeRecommendations(List<String> queryUris, int k) {
        try {
            UriComponentsBuilder builder = UriComponentsBuilder
                    .fromHttpUrl(recommendationApiUrl + "/recommend/recommend-collaborative")
                    .queryParam("k", k);

            for (String uri : queryUris) {
                builder.queryParam("query_uris", uri);
            }

            String url = builder.toUriString();
            HttpHeaders headers = createHeaders();
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<List<String>> response = restTemplate.exchange(
                url, HttpMethod.GET, entity, new ParameterizedTypeReference<List<String>>() {}
            );

            return response.getBody();
        } catch (HttpClientErrorException e) {
            handleHttpError(e, "collaborative recommendations");
            throw new RuntimeException("Failed to get collaborative recommendations");
        }
    }
    
    /**
     * Get hybrid recommendations
     */
    public List<String> getHybridRecommendations(String playlistName, List<String> queryUris, int k, int nNeighbors) {
        try {
            UriComponentsBuilder builder = UriComponentsBuilder
                    .fromHttpUrl(recommendationApiUrl + "/recommend/recommend-hybrid")
                    .queryParam("playlist_name", playlistName)
                    .queryParam("k", k)
                    .queryParam("n_neighbors", nNeighbors);

            for (String uri : queryUris) {
                builder.queryParam("query_uris", uri);
            }

            String url = builder.toUriString();
            HttpHeaders headers = createHeaders();
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<List> response = restTemplate.exchange(
                    url, HttpMethod.GET, entity, List.class);

            return response.getBody();
        } catch (HttpClientErrorException e) {
            handleHttpError(e, "hybrid recommendations");
            throw new RuntimeException("Failed to get hybrid recommendations");
        }
    }
    
    /**
     * Check if recommendation engine is healthy
     */
    public boolean isHealthy() {
        try {
            String url = recommendationApiUrl + "/health";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * Create headers with API key
     */
    private HttpHeaders createHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.set("X-API-Key", apiKey);
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }
    
    /**
     * Handle HTTP errors from FastAPI
     */
    private void handleHttpError(HttpClientErrorException e, String operation) {
        if (e.getStatusCode() == HttpStatus.UNAUTHORIZED) {
            throw new RuntimeException("Invalid API key for recommendation service");
        } else if (e.getStatusCode() == HttpStatus.NOT_FOUND) {
            throw new RuntimeException("Recommendation endpoint not found");
        } else {
            throw new RuntimeException("Error calling recommendation service for " + operation + ": " + e.getMessage());
        }
    }
}