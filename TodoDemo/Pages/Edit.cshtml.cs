using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using TodoDemo.Data;

namespace TodoDemo.Pages;

public class EditModel : PageModel
{
    private readonly TodoStore _store;

    public EditModel(TodoStore store)
    {
        _store = store;
    }

    [BindProperty]
    [Required(ErrorMessage = "請輸入待辦事項。")]
    [StringLength(120, ErrorMessage = "標題最多 120 個字元。")]
    public string EditTitle { get; set; } = string.Empty;

    public async Task<IActionResult> OnGetAsync(Guid id)
    {
        var todo = (await _store.GetAllAsync()).FirstOrDefault(item => item.Id == id);
        if (todo is null)
        {
            return NotFound();
        }

        EditTitle = todo.Title;
        return Page();
    }

    public async Task<IActionResult> OnPostAsync(Guid id)
    {
        if (!ModelState.IsValid)
        {
            return Page();
        }

        if (!await _store.UpdateAsync(id, EditTitle))
        {
            return NotFound();
        }

        TempData["Message"] = "已更新待辦事項。";
        return RedirectToPage("/Index");
    }
}
