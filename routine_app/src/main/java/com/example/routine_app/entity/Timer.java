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
    private User user;

    private String timerName;
    private LocalDate date;
    private int durationHours;
    private int durationMinutes;
    private String icon;
    private boolean completed;

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