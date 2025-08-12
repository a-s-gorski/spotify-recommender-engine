package com.example.authbackend.payload.requests;

import jakarta.validation.constraints.*;
import java.util.Set;

public record SignupRequest(
    @NotBlank
    @Size(min = 3, max = 20)
    String username,

    @NotBlank
    @Size(max = 50)
    @Email
    String email,

    Set<String> role,

    @NotBlank
    @Size(min = 6, max = 40)
    String password
) {}
