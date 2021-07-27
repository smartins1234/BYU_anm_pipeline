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

    Publish creates / versions HDAs.
    Clone will clone an HDA. (tab menu support tbd)

    on publish:
        check that 1+ nodes are selected.
        check that selected nodes are in the object level

        If one node Selected:
            If node(s) is/are not HDA:
                -if nodes are not subnet:
                    collapse nodes into subnet
                -create HDA with subnet

        Now, there is an HDA to work with.
        Ask user if they want to create a new HDA, or version an existing HDA
            -if versioning current HDA:
                pull up menu of existing HDAs
                user selects HDA to version
                program *versions up HDA*
            -else:
                prompt for HDA name
                rename HDA with new name
                save HDA


    (OLD){
    TLDR: saves versioned tool .hda with notes

    selected: hda

    Opens a dialog box and requests first tool Name, then a comment to publish the tool with (note: only lets you publish over pre-made tools)
    versions up the HDA
    adds note in HDA metadata
    Saves versioned (hda tools stored where?)
    export USD file of tool? Probably not.
    }

Shot:
    TLDR: saves versioned shot .hip with notes. Will save in project folder, regardless of where the actual file is stored. With correct name too.

    selected: nothing

    Opens a dialog box and requests first Shot Name, then a comment to publish the shot with (note: only lets you publish over pre-made shots)
    Changes hip file name to reflect current shot and version number
    Saves hip file into the /groups/cenote/BYU_anm_pipeline/production/shots/[current shot] folder
    Connects shot note and version number in the [forgot what it's called] file















_
