export function custom_apply_patches() {

    String.prototype.startswith = function (prefix, start) {
        //console.log("Custom startswith()! prefix = ", prefix, ", start = ", start);
        var pos_start = (typeof start == 'undefined' ? 0 : start);
        if (prefix instanceof Array) {
            for (var i=0;i<prefix.length;i++) {
                if (this.substr(pos_start, prefix[i].length) == prefix [i]) {
                    return true;
                }
            }
        } else {
            return (this.substr(pos_start, prefix.length) == prefix);
        }
        return false;
    };

};

