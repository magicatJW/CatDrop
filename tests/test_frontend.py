import unittest
from pathlib import Path


class FrontendBehaviorTests(unittest.TestCase):
    """確認前台必要互動未在打包前遺漏。"""

    @classmethod
    def setUpClass(cls):
        web_dir = Path(__file__).parents[1] / "web"
        cls.script = (web_dir / "app.js").read_text(encoding="utf-8")
        cls.html = (web_dir / "index.html").read_text(encoding="utf-8")
        cls.styles = (web_dir / "styles.css").read_text(encoding="utf-8")

    def test_selected_file_can_be_removed(self):
        self.assertIn('remove.className = "remove-file"', self.script)
        self.assertIn("state.files.splice(index, 1)", self.script)

    def test_upload_requires_confirmation(self):
        self.assertIn('window.confirm(text("confirmUpload"', self.script)

    def test_frontend_contains_no_logo_reference(self):
        combined = self.html + self.script + self.styles
        self.assertNotIn("logo", combined.lower())
        self.assertNotIn("CLT_", combined)

    def test_frontend_synchronizes_dynamic_configuration(self):
        self.assertIn('state.extensions = config.extensions', self.script)
        self.assertIn('state.uploadEnabled = config.uploadEnabled', self.script)
        self.assertIn('state.allowAllFileTypes = config.allowAllFileTypes', self.script)
        self.assertIn('state.allowAllFileTypes ? "" : state.extensions.join(",")', self.script)
        self.assertIn('state.allowAllFileTypes || state.extensions.includes', self.script)
        self.assertIn('setInterval(loadConfig, 3000)', self.script)
        self.assertIn('id="supportedExtensions"', self.html)
        self.assertIn('id="uploadStatus"', self.html)

    def test_paused_state_disables_upload_controls(self):
        self.assertIn('fileInput.disabled = !state.uploadEnabled', self.script)
        self.assertIn('request.status === 503', self.script)
        self.assertIn('.drop-zone.disabled', self.styles)

    def test_control_panel_supports_sorting_and_drag_selection(self):
        source = (Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")
        self.assertIn('selectmode="extended"', source)
        self.assertIn('self.tree.bind("<B1-Motion>"', source)
        self.assertIn('command=lambda selected=column: self._sort_by(selected)', source)
        self.assertIn('window.show_toggle_var', source)
        self.assertIn('window.allow_all_file_types_var', source)
        self.assertIn('window.extension_checkbuttons', source)


if __name__ == "__main__":
    unittest.main()
