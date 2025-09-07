def register(ui, plugin_tabs):
    def content():
        ui.label('Hello from plugin!')
        # Możesz dodać tu dowolny kontent
    plugin_tabs.append(('Plugin', content))