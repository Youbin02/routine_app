package com.example.routine_app.service;

import com.example.routine_app.entity.Timer;
import com.example.routine_app.entity.User;
import com.example.routine_app.repository.TimerRepository;
import com.example.routine_app.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TimerService {
    @Autowired
    private TimerRepository timerRepository;

    @Autowired
    private UserRepository userRepository;

    //타이머 추가 메서드
    public Timer saveTimer(Timer timer, Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        timer.setUser(user);
        return timerRepository.save(timer);
    }

    public List<Timer> getUserTimers(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return timerRepository.findByUser(user);
    }

    // 타이머 수정 메서드
    public Timer updateTimer(Long timerId, Timer updatedTimer) {
        Timer timer = timerRepository.findById(timerId)
                .orElseThrow(() -> new RuntimeException("Timer not found"));

        // 수정할 필드 업데이트
        timer.setTimerName(updatedTimer.getTimerName());
        timer.setDate(updatedTimer.getDate());
        timer.setDurationHours(updatedTimer.getDurationHours());
        timer.setDurationMinutes(updatedTimer.getDurationMinutes());
        timer.setIcon(updatedTimer.getIcon());
        timer.setCompleted(updatedTimer.isCompleted());

        return timerRepository.save(timer);
    }

    // 타이머 삭제 메서드
    public void deleteTimer(Long timerId) {
        Timer timer = timerRepository.findById(timerId)
                .orElseThrow(() -> new RuntimeException("Timer not found"));
        timerRepository.delete(timer);
    }
}