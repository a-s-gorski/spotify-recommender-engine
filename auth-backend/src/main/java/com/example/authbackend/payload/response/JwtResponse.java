package com.example.authbackend.payload.response;

import java.util.List;

public record JwtResponse(
    String accessToken,
    String tokenType,
    String refreshToken,
    Long id,
    String username,
    String email,
    List<String> roles
) {}
