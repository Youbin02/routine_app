package com.example.routine_app.entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.LocalTime;

@Entity
public class Routine {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;              // 루틴 사용자 구분

    private String groupRoutineName; // 상위 루틴 이름 (세부 루틴들을 묶는 분류)
    private String routineName;     // 루틴 세부 내용
    private LocalDate date;         // 루틴 날짜
    private LocalTime startTime;    // 루틴 시작 시간
    private int durationHours;      // 루틴 지속 시간 (hour)
    private int durationMinutes;    // 루틴 지속 시간 (minute)
    private String icon;            // 루틴 LCD 아이콘 이름
    private boolean completed;      // 루틴 완료 여부

    // 기본 생성자
    public Routine() {}

    // Getter
    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public String getGroupRoutineName() {
        return groupRoutineName;
    }

    public String getRoutineName() {
        return routineName;
    }

    public LocalDate getDate() {
        return date;
    }

    public LocalTime getStartTime() {
        return startTime;
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

    public void setGroupRoutineName(String groupRoutineName) {
        this.groupRoutineName = groupRoutineName;
    }

    public void setRoutineName(String routineName) {
        this.routineName = routineName;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public void setStartTime(LocalTime startTime) {
        this.startTime = startTime;
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
