App = Em.Application.create();


App.Dossier = Em.Object.extend({
    owner_hash: null,
    access_hash: null,
    content: null
});


App.UsernameField = Em.TextField.extend();

App.ContentField = Em.TextField.extend();

App.PasswordField = Em.TextField.extend({
    insertNewline: function() {
        App.editorController.loadDossier();
    }
});


App.editorController = Em.Object.create({
    username: '',
    password: '',
    content: '',
    loadDossier: function() {
        var me = this;
        var username = me.get("username");
        var password = me.get("password");
        if ( username && password ) {
            var url = 'http://localhost:6543/load.json'
                url += '?owner_hash=%@&access_hash=%@'.fmt(me.get("username"), me.get("password"));
            $.getJSON(url,function(data) {
                $(data).each(function(index, value) {
                    var d = App.Dossier.create({
                        owner_hash: value.owner_hash,
                        access_hash: value.access_hash,
                        content: value.content
                    });
                    me.set("content", d.content);
                })
            });
        }
    }
});
