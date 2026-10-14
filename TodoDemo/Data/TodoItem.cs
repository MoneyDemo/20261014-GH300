namespace TodoDemo.Data;

public sealed record TodoItem(Guid Id, string Title, bool IsCompleted);
