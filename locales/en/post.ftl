# Main menu
btn-create-post = Create Post
btn-my-posts = My Posts

# Post wizard
choose-post-type = Step 1 of 3 — Choose post type:
btn-photo = Photo
btn-video = Video
btn-text = Text
btn-gif = GIF
btn-cancel = Cancel
btn-skip = No buttons

send-text-content = Step 2 of 3 — Send me the text for your post (max 1024 chars):
send-photo-content = Step 2 of 3 — Send me a photo (you can add a caption):
send-video-content = Step 2 of 3 — Send me a video (you can add a caption):
send-gif-content = Step 2 of 3 — Send me a GIF (you can add a caption):

send-buttons-dsl = Step 3 of 3 — 🔗 Add buttons with links.

    Each line is one button:
    <code>{"["}Label + URL]</code>

    🎨 Want a colored button? Add a color:
    <code>{"["}Label + URL + green]</code>

    Colors: 🟢 green, 🔴 red, 🔵 blue

btn-share = Share
post-saved-header = Post saved! Use:

preview-title = Here's how your post will look.

    Happy with it? Tap "Save post".
    Want to change buttons? Send them again in <code>[Label + URL]</code> format.
btn-confirm = Save post
btn-edit = Start over

wizard-cancelled = Cancelled.

wrong-content-type = Wrong content type. Please send { $expected_type }.
invalid-dsl = Invalid button format.
    Make sure each button follows this format:
    <code>{"["}Label + https://url]</code>
text-too-long = Text is too long (max 1024 characters).
internal-error = Something went wrong, please try again.

# My posts
my-posts-title = Your posts ({ $count } total):
my-posts-empty = You have no posts yet.
btn-preview = Preview
btn-delete = Delete
btn-next-page = Next ->
btn-prev-page = <- Back
delete-confirm = Are you sure you want to delete this post?
post-deleted = Post deleted.
btn-delete-yes = Yes, delete
post-actions-hint = You can delete this post using the button below.
btn-back-to-list = Back to list
btn-back-to-menu = Back to menu

# Inline
open-bot-to-create-post = Open bot to create a post
inline-not-found = Post not found. Check the key.

# Help
help-text = How to use PostMagnet:

    1. Tap "Create Post" and choose a type (text, photo, video, GIF)
    2. Send your content
    3. Add buttons with links (optional)
    4. Confirm — you'll get a unique key

    To share a post, type in any chat's message field:
    @{ $bot_username } key

    /start — main menu
    /settings — settings
    /referral — referral link
