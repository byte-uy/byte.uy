function notify(message, timeout = 3000)
{
    const alert = document.createElement('div');
    alert.className = 'terminal-alert terminal-alert-error';
    alert.textContent = message;

    const notificationContainer = document.getElementById('notification-container');
    notificationContainer.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, timeout);
}