using System.Text.Json;

namespace TodoDemo.Data;

public sealed class TodoStore
{
    private static readonly JsonSerializerOptions JsonOptions = new() { WriteIndented = true };
    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly string _filePath;

    public TodoStore(IWebHostEnvironment environment)
    {
        _filePath = Path.Combine(environment.ContentRootPath, "App_Data", "todos.json");
    }

    public async Task<IReadOnlyList<TodoItem>> GetAllAsync()
    {
        await _gate.WaitAsync();
        try
        {
            return await LoadAsync();
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task AddAsync(string title)
    {
        var normalizedTitle = NormalizeTitle(title);
        await _gate.WaitAsync();
        try
        {
            var todos = await LoadAsync();
            todos.Add(new TodoItem(Guid.NewGuid(), normalizedTitle, false));
            await SaveAsync(todos);
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task<bool> UpdateAsync(Guid id, string title)
    {
        var normalizedTitle = NormalizeTitle(title);
        await _gate.WaitAsync();
        try
        {
            var todos = await LoadAsync();
            var index = todos.FindIndex(todo => todo.Id == id);
            if (index < 0)
            {
                return false;
            }

            todos[index] = todos[index] with { Title = normalizedTitle };
            await SaveAsync(todos);
            return true;
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task<bool> ToggleAsync(Guid id)
    {
        await _gate.WaitAsync();
        try
        {
            var todos = await LoadAsync();
            var index = todos.FindIndex(todo => todo.Id == id);
            if (index < 0)
            {
                return false;
            }

            todos[index] = todos[index] with { IsCompleted = !todos[index].IsCompleted };
            await SaveAsync(todos);
            return true;
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task<bool> DeleteAsync(Guid id)
    {
        await _gate.WaitAsync();
        try
        {
            var todos = await LoadAsync();
            var removed = todos.RemoveAll(todo => todo.Id == id) > 0;
            if (removed)
            {
                await SaveAsync(todos);
            }

            return removed;
        }
        finally
        {
            _gate.Release();
        }
    }

    private async Task<List<TodoItem>> LoadAsync()
    {
        if (!File.Exists(_filePath))
        {
            return [];
        }

        await using var stream = File.OpenRead(_filePath);
        return await JsonSerializer.DeserializeAsync<List<TodoItem>>(stream, JsonOptions) ?? [];
    }

    private async Task SaveAsync(List<TodoItem> todos)
    {
        var directory = Path.GetDirectoryName(_filePath)!;
        Directory.CreateDirectory(directory);

        var temporaryPath = $"{_filePath}.{Guid.NewGuid():N}.tmp";
        try
        {
            await using (var stream = File.Create(temporaryPath))
            {
                await JsonSerializer.SerializeAsync(stream, todos, JsonOptions);
            }

            File.Move(temporaryPath, _filePath, true);
        }
        finally
        {
            if (File.Exists(temporaryPath))
            {
                File.Delete(temporaryPath);
            }
        }
    }

    private static string NormalizeTitle(string title)
    {
        var normalizedTitle = title.Trim();
        if (normalizedTitle.Length is 0 or > 120)
        {
            throw new ArgumentException("標題長度必須介於 1 到 120 個字元。", nameof(title));
        }

        return normalizedTitle;
    }
}
