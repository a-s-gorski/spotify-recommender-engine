package com.example.authbackend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;

@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();

        HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory();
        factory.setConnectTimeout(20000); // 20 seconds
        factory.setReadTimeout(40000); // 40 seconds
        factory.setConnectionRequestTimeout(20000); // 20 seconds
        restTemplate.setRequestFactory(factory);
        return restTemplate;
    }
}
