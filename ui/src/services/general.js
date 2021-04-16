export function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2)
        return parts
        .pop()
        .split(";")
        .shift();
}

export function search(data, keys, text) {
    var obj = [];
    if (data) {
      for (var i = 0; i < data.length; i++) {
        for (var j = 0; j < keys.length; j++) {
          if (data[i][keys[j]]) {
            if (
              data[i][keys[j]]
                .toString()
                .toLowerCase()
                .indexOf(text.toLowerCase()) !== -1
            ) {
              obj.push(data[i]);
              break;
            }
          }
        }
      }
    }
    return obj;
  }