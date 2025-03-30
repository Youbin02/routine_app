package com.example.routine_app.controller;

import com.example.routine_app.entity.Timer;
import com.example.routine_app.service.TimerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/timers")
public class TimerController {
    @Autowired
    private TimerService timerService;

    //타이머 추가 엔드포인트
    @PostMapping("/{userId}")
    public Timer createTimer(@RequestBody Timer timer, @PathVariable Long userId) {
        return timerService.saveTimer(timer, userId);
    }

    @GetMapping("/{userId}")
    public List<Timer> getUserTimers(@PathVariable Long userId) {
        return timerService.getUserTimers(userId);
    }

    // 타이머 수정 엔드포인트
    @PutMapping("/{timerId}")
    public Timer updateTimer(@PathVariable Long timerId, @RequestBody Timer timer) {
        return timerService.updateTimer(timerId, timer);
    }

    // 타이머 삭제 엔드포인트
    @DeleteMapping("/{timerId}")
    public void deleteTimer(@PathVariable Long timerId) {
        timerService.deleteTimer(timerId);
    }
}