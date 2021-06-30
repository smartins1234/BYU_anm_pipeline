This tool is being developed from the DCC tools. Martin Edwards is spearheading it LIKE A BOSS!!!
June 9: Started reading code


Here's a quick overview of what the publisher tools do:


Asset:
    update: I think
    1) display list of current assets that are publishable to

    have selected: nodes in the object context
    loop through nodes: pull object nodes into LOPs
    merge those nodes: render out as usd (saved with a version number and .element info)
    group selected nodes into subnet
    save subnet as versioned HDA into the right folder.

    this workflow won't make it possible to import assets via the tab menu , but versioning will be preserved.
    Or should there be a previously selected subnetwork? I feel like that would be helpful...

    Create: creates folders and hda with given name. Creates empty HDA ready to be filled. Thus, things only must be created inside the subnet, then saved out. A new HDA would be created each time, without my versioning system, but that should work anyway.

    Still unclear on this one...
    My guess:
    Takes assembled asset and versions up the current hda it's connected to.
    Also, export a USD file from the result of the asset.



Tool:
    TLDR: saves versioned tool .hda with notes

    selected: hda

    Opens a dialog box and requests first tool Name, then a comment to publish the tool with (note: only lets you publish over pre-made tools)
    versions up the HDA
    adds note in HDA metadata
    Saves versioned (hda tools stored where?)
    export USD file of tool? Probably not.

Shot:
    TLDR: saves versioned shot .hip with notes

    selected: nothing

    Opens a dialog box and requests first Shot Name, then a comment to publish the shot with (note: only lets you publish over pre-made shots)
    Changes hip file name to reflect current shot and version number
    Saves hip file into the /groups/cenote/BYU_anm_pipeline/production/shots/[current shot] folder
    Connects shot note and version number in the [forgot what it's called] file















_
