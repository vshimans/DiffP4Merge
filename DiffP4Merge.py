import sublime
import sublime_plugin
import os
import tempfile
import subprocess

class DiffP4mergeCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Determine which two views to compare.
        groups = self.window.num_groups()
        if groups >= 2:
            view1 = self.window.active_view_in_group(0)
            view2 = self.window.active_view_in_group(1)
            if not view1 or not view2:
                sublime.error_message("Ensure both groups have an active view.")
                return
        else:
            # If only one group, use the active view and the most recently used (other) view.
            active_view = self.window.active_view()
            views = [v for v in self.window.views() if v.id() != active_view.id()]
            if not views:
                sublime.error_message("Need at least 2 open tabs for diff.")
                return
            view1 = active_view
            view2 = views[0]

        # Determine file paths for each view.
        file1 = self.get_view_path(view1, "sublime_diff1.txt")
        file2 = self.get_view_path(view2, "sublime_diff2.txt")

        if file1 is None or file2 is None:
            return

        # Path to P4Merge executable.
        settings = sublime.load_settings('DiffP4merge.sublime-settings')
        p4merge_exe = settings.get('p4merge_path', '')

        if not p4merge_exe or not os.path.isfile(p4merge_exe):
            sublime.error_message("Please configure 'p4merge_path' in DiffP4merge.sublime-settings correctly.")
            return

        try:
            subprocess.Popen([p4merge_exe, file1, file2])
        except Exception as e:
            sublime.error_message("Failed to launch P4Merge:\n" + str(e))

    def get_view_path(self, view, temp_file_name):
        """
        Returns the file path for the view. If the view has been saved to disk and has no unsaved changes,
        the real file path is returned. Otherwise, the view's contents are written
        to a temporary file and its path is returned.
        """
        if view.file_name() and not view.is_dirty():
            # Use the actual file if it exists and has no unsaved modifications.
            return view.file_name()
        else:
            # For unsaved or modified files, use a temporary file.
            content = view.substr(sublime.Region(0, view.size()))
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, temp_file_name)
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                sublime.error_message("Error writing temporary file for unsaved or modified view:\n" + str(e))
                return None
            return temp_file
