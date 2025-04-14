package com.example.routine_app.entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.LocalTime;

@Entity
public class Timer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;              // 타이머 사용자 구분

    private String timerName;       // 타이머 내용
    private LocalDate date;         // 타이머 날짜
    private int durationHours;      // 타이머 지속 시간 (hour)
    private int durationMinutes;    // 타이머 지속 시간 (minute)
    private String icon;            // 타이머 LCD 아이콘 이름
    private boolean completed;      // 타이머 달성 여부
    
    // 기본 생성자
    public Timer() {}

    // Getter
    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public String getTimerName() {
        return timerName;
    }

    public LocalDate getDate() {
        return date;
    }

    public int getDurationHours() {
        return durationHours;
    }

    public int getDurationMinutes() {
        return durationMinutes;
    }

    public String getIcon() {
        return icon;
    }

    public boolean isCompleted() {
        return completed;
    }

    // Setter
    public void setId(Long id) {
        this.id = id;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public void setTimerName(String timerName) {
        this.timerName = timerName;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public void setDurationHours(int durationHours) {
        this.durationHours = durationHours;
    }

    public void setDurationMinutes(int durationMinutes) {
        this.durationMinutes = durationMinutes;
    }

    public void setIcon(String icon) {
        this.icon = icon;
    }

    public void setCompleted(boolean completed) {
        this.completed = completed;
    }
}
