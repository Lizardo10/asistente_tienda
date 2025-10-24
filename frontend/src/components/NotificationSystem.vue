<template>
  <div class="notifications-container">
    <TransitionGroup name="notification" tag="div">
      <div
        v-for="notification in notifications.items"
        :key="notification.id"
        :class="[
          'notification',
          `notification-${notification.type}`
        ]"
        @click="removeNotification(notification.id)"
      >
        <div class="notification-icon">
          <i :class="getNotificationIcon(notification.type)"></i>
        </div>
        <div class="notification-content">
          <p class="notification-message">{{ notification.message }}</p>
          <p class="notification-time">{{ formatTime(notification.timestamp) }}</p>
        </div>
        <button 
          class="notification-close"
          @click.stop="removeNotification(notification.id)"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { notifications, removeNotification } from '../services/cart_enhanced'

function getNotificationIcon(type) {
  const icons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return icons[type] || icons.info
}

function formatTime(timestamp) {
  const now = new Date()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  
  if (seconds < 60) {
    return 'Ahora'
  } else if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}m`
  } else {
    return timestamp.toLocaleTimeString()
  }
}
</script>

<style scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  border-left: 4px solid;
}

.notification:hover {
  transform: translateX(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.notification-success {
  border-left-color: #10b981;
}

.notification-error {
  border-left-color: #ef4444;
}

.notification-warning {
  border-left-color: #f59e0b;
}

.notification-info {
  border-left-color: #3b82f6;
}

.notification-icon {
  margin-right: 12px;
  font-size: 20px;
}

.notification-success .notification-icon {
  color: #10b981;
}

.notification-error .notification-icon {
  color: #ef4444;
}

.notification-warning .notification-icon {
  color: #f59e0b;
}

.notification-info .notification-icon {
  color: #3b82f6;
}

.notification-content {
  flex: 1;
}

.notification-message {
  margin: 0 0 4px 0;
  font-weight: 500;
  color: #1f2937;
}

.notification-time {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}

.notification-close {
  margin-left: 12px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.notification-close:hover {
  color: #374151;
}

/* Animaciones */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>
