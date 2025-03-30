package com.example.routine_app.service;

import com.example.routine_app.entity.Routine;
import com.example.routine_app.entity.User;
import com.example.routine_app.repository.RoutineRepository;
import com.example.routine_app.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RoutineService {
    @Autowired
    private RoutineRepository routineRepository;

    @Autowired
    private UserRepository userRepository;

    //루틴 추가 메서드
    public Routine saveRoutine(Routine routine, Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        routine.setUser(user);
        return routineRepository.save(routine);
    }

    public List<Routine> getUserRoutines(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return routineRepository.findByUser(user);
    }

    // 루틴 수정 메서드
    public Routine updateRoutine(Long routineId, Routine updatedRoutine) {
        Routine routine = routineRepository.findById(routineId)
                .orElseThrow(() -> new RuntimeException("Routine not found"));

        // 수정할 필드 업데이트
        routine.setRoutineName(updatedRoutine.getRoutineName());
        routine.setDate(updatedRoutine.getDate());
        routine.setStartTime(updatedRoutine.getStartTime());
        routine.setDurationHours(updatedRoutine.getDurationHours());
        routine.setDurationMinutes(updatedRoutine.getDurationMinutes());
        routine.setIcon(updatedRoutine.getIcon());
        routine.setCompleted(updatedRoutine.isCompleted());

        return routineRepository.save(routine);
    }

    // 루틴 삭제 메서드
    public void deleteRoutine(Long routineId) {
        Routine routine = routineRepository.findById(routineId)
                .orElseThrow(() -> new RuntimeException("Routine not found"));
        routineRepository.delete(routine);
    }
}