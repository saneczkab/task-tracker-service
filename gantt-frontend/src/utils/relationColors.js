const COLORS = [
  "#FFE5E5",
  "#E5F5FF",
  "#FFF5E5",
  "#E5FFE5",
  "#F5E5FF",
  "#FFFFE5",
  "#E5FFFF",
  "#FFE5F5",
  "#F5FFE5",
  "#FFE5FF",
  "#E5F5E5",
  "#FFF5F5",
];

export function generateRelationColors(tasks) {
  const taskColorMap = {};
  const groups = [];

  const tasksWithRelations = tasks.filter(
    (task) => task.relations && task.relations.length > 0,
  );

  if (tasksWithRelations.length === 0) {
    return taskColorMap;
  }

  const taskToGroup = new Map();

  tasksWithRelations.forEach((task) => {
    task.relations.forEach((relation) => {
      const taskId1 = relation.task_id_1;
      const taskId2 = relation.task_id_2;

      const group1 = taskToGroup.get(taskId1);
      const group2 = taskToGroup.get(taskId2);

      if (!group1 && !group2) {
        const newGroup = new Set([taskId1, taskId2]);
        groups.push(newGroup);
        taskToGroup.set(taskId1, newGroup);
        taskToGroup.set(taskId2, newGroup);
      } else if (group1 && !group2) {
        group1.add(taskId2);
        taskToGroup.set(taskId2, group1);
      } else if (!group1 && group2) {
        group2.add(taskId1);
        taskToGroup.set(taskId1, group2);
      } else if (group1 !== group2) {
        group2.forEach((taskId) => {
          group1.add(taskId);
          taskToGroup.set(taskId, group1);
        });

        const idx = groups.indexOf(group2);
        if (idx !== -1) {
          groups.splice(idx, 1);
        }
      }
    });
  });

  groups.forEach((group, index) => {
    const color = COLORS[index % COLORS.length];
    group.forEach((taskId) => {
      taskColorMap[taskId] = color;
    });
  });

  return taskColorMap;
}
