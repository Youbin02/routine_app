package com.example.routine_app.controller;

import com.example.routine_app.entity.Routine;
import com.example.routine_app.service.RoutineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/routines")
public class RoutineController {
    @Autowired
    private RoutineService routineService;

    //루틴 추가 엔드포인트
    @PostMapping("/{userId}")
    public Routine createRoutine(@RequestBody Routine routine, @PathVariable Long userId) {
        return routineService.saveRoutine(routine, userId);
    }

    @GetMapping("/{userId}")
    public List<Routine> getUserRoutines(@PathVariable Long userId) {
        return routineService.getUserRoutines(userId);
    }

    // 루틴 수정 엔드포인트
    @PutMapping("/{routineId}")
    public Routine updateRoutine(@PathVariable Long routineId, @RequestBody Routine routine) {
        return routineService.updateRoutine(routineId, routine);
    }

    // 루틴 삭제 엔드포인트
    @DeleteMapping("/{routineId}")
    public void deleteRoutine(@PathVariable Long routineId) {
        routineService.deleteRoutine(routineId);
    }
}