package com.example.routine_app.repository;

import com.example.routine_app.entity.Routine;
import com.example.routine_app.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface RoutineRepository extends JpaRepository<Routine, Long> {
    List<Routine> findByUser(User user);
}