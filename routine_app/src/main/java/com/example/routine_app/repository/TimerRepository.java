package com.example.routine_app.repository;

import com.example.routine_app.entity.Timer;
import com.example.routine_app.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface TimerRepository extends JpaRepository<Timer, Long> {
    List<Timer> findByUser(User user);
}