package com.example.authbackend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOrigins("http://localhost:5173", "http://localhost", "https://localhost:5173", "https://0.0.0.0:5173", "http://0.0.0.0:5173", "http://localhost:5173", "http://127.0.0.1:5173", "https://127.0.0.1:5173", "http://127.0.0.1:*",
                        "http://localhost:80", "https://localhost:80", "https://0.0.0.0:80", "http://0.0.0.0:80", "http://localhost:80", "http://127.0.0.1:80", "https://127.0.0.1:80", "http://127.0.0.1:*", "http://127.0.0.1")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        .allowedHeaders("*")
                        .allowCredentials(true);
            }
        };
    }
}