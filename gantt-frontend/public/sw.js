self.addEventListener("push", (event) => {
  const data = event.data.json();

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      data: {
        team_id: data.team_id,
        stream_id: data.stream_id,
      },
    }),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const teamId = event.notification.data.team_id;
  const streamId = event.notification.data.stream_id;
  const url = `/team/${teamId}/stream/${streamId}`;

  event.waitUntil(clients.openWindow(url));
});
