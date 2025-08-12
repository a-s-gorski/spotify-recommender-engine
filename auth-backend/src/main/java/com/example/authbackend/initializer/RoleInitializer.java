package com.example.authbackend.initializer;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.example.authbackend.models.ERole;
import com.example.authbackend.repository.RoleRepository;
import com.example.authbackend.models.Role;
import jakarta.annotation.PostConstruct;

@Component
public class RoleInitializer {
    private final RoleRepository roleRepository;

    public RoleInitializer(RoleRepository roleRepository) {
        this.roleRepository = roleRepository;
    }

    @PostConstruct
    public void initRoles() {
        for (ERole roleEnum : ERole.values()) {
            roleRepository.findByName(roleEnum).orElseGet(() -> {
                Role role = new Role();
                role.setName(roleEnum);
                return roleRepository.save(role);
            });
        }
    }
    
}
