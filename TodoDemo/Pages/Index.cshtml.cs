using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using System.ComponentModel.DataAnnotations;
using TodoDemo.Data;

namespace TodoDemo.Pages;

public class IndexModel : PageModel
{
    private readonly TodoStore _store;

    public IndexModel(TodoStore store)
    {
        _store = store;
    }

    [BindProperty]
    [Required(ErrorMessage = "請輸入待辦事項。")]
    [StringLength(120, ErrorMessage = "標題最多 120 個字元。")]
    public string NewTitle { get; set; } = string.Empty;

    public IReadOnlyList<TodoItem> Todos { get; private set; } = [];

    public int RemainingCount => Todos.Count(todo => !todo.IsCompleted);

    public async Task OnGetAsync()
    {
        await LoadTodosAsync();
    }

    public async Task<IActionResult> OnPostAddAsync()
    {
        if (!ModelState.IsValid)
        {
            await LoadTodosAsync();
            return Page();
        }

        await _store.AddAsync(NewTitle);
        TempData["Message"] = "已新增待辦事項。";
        return RedirectToPage();
    }

    public async Task<IActionResult> OnPostToggleAsync(Guid id)
    {
        await _store.ToggleAsync(id);
        return RedirectToPage();
    }

    public async Task<IActionResult> OnPostDeleteAsync(Guid id)
    {
        await _store.DeleteAsync(id);
        TempData["Message"] = "已刪除待辦事項。";
        return RedirectToPage();
    }

    private async Task LoadTodosAsync()
    {
        Todos = await _store.GetAllAsync();
    }
}
