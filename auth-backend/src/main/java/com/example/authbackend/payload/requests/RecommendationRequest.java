package com.example.authbackend.payload.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Positive;

import java.util.List;

public record RecommendationRequest(
    @NotBlank String playlistName,
    @NotEmpty List<String> queryUris,
    @Positive int k,
    int nNeighbors
) {}
