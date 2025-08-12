package com.example.authbackend.controllers;

import com.example.authbackend.services.RecommendationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {

    @Autowired
    private RecommendationService recommendationService;

    @GetMapping("/clustering")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> getClusteringRecommendations(
            @RequestParam String playlistName,
            @RequestParam(defaultValue = "10") int k,
            @RequestParam(defaultValue = "5") int nNeighbors) {
        
        try {
            List<String> recommendations = recommendationService.getClusteringRecommendations(
                playlistName, k, nNeighbors);
            return ResponseEntity.ok(recommendations);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Failed to get clustering recommendations: " + e.getMessage()));
        }
    }

    @GetMapping("/collaborative")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> getCollaborativeRecommendations(
            @RequestParam List<String> queryUris,
            @RequestParam(defaultValue = "10") int k) {
        
        try {
            List<String> recommendations = recommendationService.getCollaborativeRecommendations(queryUris, k);
            return ResponseEntity.ok(recommendations);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Failed to get collaborative recommendations: " + e.getMessage()));
        }
    }

    @GetMapping("/hybrid")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> getHybridRecommendations(
            @RequestParam String playlistName,
            @RequestParam List<String> queryUris,
            @RequestParam(defaultValue = "10") int k,
            @RequestParam(defaultValue = "5") int nNeighbors) {
        
        try {
            List<String> recommendations = recommendationService.getHybridRecommendations(
                playlistName, queryUris, k, nNeighbors);
            return ResponseEntity.ok(recommendations);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Failed to get hybrid recommendations: " + e.getMessage()));
        }
    }

    @GetMapping("/health")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> checkRecommendationEngineHealth() {
        try {
            boolean isHealthy = recommendationService.isHealthy();
            return ResponseEntity.ok(Map.of(
                "status", isHealthy ? "healthy" : "unhealthy",
                "service", "recommendation-engine"
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Health check failed: " + e.getMessage()));
        }
    }
}