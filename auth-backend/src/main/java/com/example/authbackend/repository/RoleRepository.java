package com.example.authbackend.repository;

import java.util.Optional;

import com.example.authbackend.models.ERole;
import com.example.authbackend.models.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RoleRepository extends JpaRepository<Role, Long> {
    Optional<Role> findByName(ERole name);
}