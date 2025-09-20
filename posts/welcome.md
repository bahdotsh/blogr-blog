---
title: "Welcome to My Blog"
date: "2025-09-20"
author: "bahdotsh"
description: "Welcome to bah! This is your first blog post to help you get started."
tags: ["welcome", "getting-started", "first-post"]
status: "published"
slug: "welcome"
featured: true
---

# Welcome to bah!

Congratulations! 🎉 You've successfully set up your new blog with **Blogr**. This is your first blog post, and it's here to help you understand how everything works.

## What is Blogr?

Blogr is a modern CLI static site generator specifically designed for blogs. It focuses on:

- **Simplicity** - Easy to use command-line interface
- **Speed** - Fast builds and optimized output
- **Developer Experience** - Live reload, hot reloading, and great tooling
- **Themes** - Beautiful, customizable themes
- **GitHub Integration** - Seamless deployment to GitHub Pages

## Getting Started

Here are some commands to help you get started:

### Create a New Post

```bash
blogr new "My Second Post"
```

This will create a new markdown file in your `posts/` directory with the proper front matter.

### Start Development Server

```bash
blogr serve
```

This starts a local development server with live reload. Any changes you make to your posts or configuration will automatically update in your browser.

### Build Your Site

```bash
blogr build
```

This generates the static files for your blog in the `dist/` directory.

### Deploy to GitHub Pages

```bash
blogr deploy
```

This builds and deploys your site to GitHub Pages automatically.

## Writing Posts

All your blog posts go in the `posts/` directory as Markdown files. Each post needs **front matter** at the top with metadata:

```yaml
---
title: "Your Post Title"
date: "2024-01-15"
author: "Your Name"
description: "Brief description for SEO and previews"
tags: ["tag1", "tag2", "tag3"]
status: "published"  # or "draft"
slug: "url-friendly-slug"
featured: false      # Set to true for featured posts
---
```

### Supported Markdown Features

Blogr supports all standard Markdown features plus some extras:

- **Headers** - Use `#`, `##`, `###`, etc.
- **Links** - `[Link text](https://example.com)`
- **Images** - `![Alt text](path/to/image.png)`
- **Code blocks** - Syntax highlighting included
- **Tables** - Standard markdown table syntax
- **Lists** - Both ordered and unordered

### Code Syntax Highlighting

Code blocks are automatically highlighted:

```rust
fn main() {
    println!("Hello, Blogr!");
}
```

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## Customizing Your Blog

### Theme Configuration

Your blog uses the **Minimal Retro** theme. You can customize colors, fonts, and other settings in your `blogr.toml` file:

```toml
[theme.config]
primary_color = "#FF6B35"
secondary_color = "#F7931E"
background_color = "#2D1B0F"
font_family = "Monaco, 'Courier New', monospace"
show_reading_time = true
show_author = true
```

### Static Files

Put images, custom CSS, JavaScript, and other static files in the `static/` directory. They'll be copied to your built site automatically.

## Project Structure

```
your-blog/
├── blogr.toml          # Configuration
├── posts/              # Your blog posts
│   ├── welcome.md      # This post
│   └── about.md        # About page
├── static/             # Static assets
│   ├── images/
│   ├── css/
│   └── js/
├── themes/             # Custom theme files (optional)
└── dist/               # Built site (generated)
```

## Tips for Blogging Success

1. **Write consistently** - Regular posting keeps readers engaged
2. **Use good titles** - Make them descriptive and SEO-friendly
3. **Add descriptions** - These appear in previews and search results
4. **Use tags wisely** - Help readers find related content
5. **Include images** - Visual content makes posts more engaging
6. **Preview before publishing** - Use `blogr serve` to check how posts look

## Next Steps

Now that you have Blogr set up, here are some things you might want to do:

1. **Edit this post** - Customize it or delete it entirely
2. **Create your About page** - Tell readers about yourself
3. **Write your first real post** - Share something you're passionate about
4. **Customize your theme** - Make it match your personal style
5. **Set up deployment** - Get your blog online for the world to see

## Need Help?

- Check out the [Blogr documentation](https://github.com/bahdotsh/blogr)
- Run `blogr --help` for command reference
- Use `blogr project check` to validate your setup

---

Happy blogging! 🚀

*This post was automatically generated when you initialized your Blogr project. Feel free to edit or delete it.*
