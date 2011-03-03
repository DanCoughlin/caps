/*
 * hides the elements that display the file upload is a 
 * zip file and can be unzipped on upload 
 */
function hideZipDialog(id) {
    $('#error_ff_'+id).hide();
}


/*
 * add a form element that will allow a user to upload
 * additional files
 */
function addFileInput() {
    var fi_dupe = new Object();
    fi_dupe['updateIds'] = ["ff_1", "file_1", "base_name_1", "unzip_cb_1", "error_ff_1"];
    fi_dupe['prefixIds'] = ["ff_", "file_", "base_name_", "unzip_cb_", "error_ff_"];
    fi_dupe['nodeId'] = 'ff_1';
    fi_dupe['nodePrefix'] = 'ff_';
    fi_dupe['countId'] = 'upload_count';

    var nxtId = addFormElement(fi_dupe);

    // hide the zip elements 
    hideZipDialog(nxtId);
}


/*
 * this function adds the necessary elements to
 * add more metadata
 */
function addMetaInput() {
    var md_dupe = new Object();
    md_dupe['updateIds'] = ['md_1', 'meta_type_1', 'meta_value_1'];
    md_dupe['prefixIds'] = ['md_', 'meta_type_', 'meta_value_'];
    md_dupe['nodeId'] = 'md_1';
    md_dupe['nodePrefix'] = 'md_';
    md_dupe['countId'] = 'metadata_count';
    addFormElement(md_dupe);
}


/* 
 * function takes an object and adds a form element 
 * based on the values of that object
 *
 * duplicate.updateIds => array of ids to increment value of
 * duplicate.prefixIds => prefix that doesnt include the increment
 *          suffix, of ids to increment
 * duplicate.nodeId => node that we will duplicate
 * duplicate.nodePrefix => prefix of node to duplicate, not including
 *          the suffix that indicates which element number this is
 * duplicate.countId => id of the form element that is keeping track 
 *           of the number of elements we have duplicated
 * 
 * SPAN elements will be cleared when duplicated.  The inner 
 * HTML will be blank on all SPAN elements.
 */
function addFormElement(duplicate) {
    var cv = $('#'+duplicate.countId).attr("value");

    var cloneNode = $('#'+duplicate.nodeId).clone();
    var nxtId = parseInt(cv) + 1;
    cloneNode.attr("id", duplicate.nodePrefix+nxtId);

    for (var i=0; i < duplicate.updateIds.length; i++) {
        newId = duplicate.prefixIds[i] + nxtId;
        var elem = cloneNode.find('#'+duplicate.updateIds[i]);
        elem.attr("id", newId); 
        // if element has a name attribute - update as well
        if (elem.attr("name")) {
            elem.attr("name", newId); 
        }
        
        // clear any potential value carry overs
        if (elem.is("input")) {
            elem.attr("value", "");
        } 
        else if (elem.is("select")) {
            elem.attr("selectedIndex", 0);
        }
        // any span element will be cleared
        else if (elem.is("span")) {
            elem.html("");
        }
    }
   
    cloneNode.insertAfter('#'+duplicate.nodePrefix+cv);

    $('#'+duplicate.countId).attr("value", nxtId); 

    return nxtId;
}
