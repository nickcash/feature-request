/**
 * Master ViewModel for KnockoutJS
 */
var ViewModel = function() {
    //Creates and binds ViewModel with Knockout

    this.activeClient = ko.observable();
    this.clients = ko.observableArray([]);
    this.productAreas = ko.observableArray();
    this.productAreaMap = {};
    this.clientRequests = ko.observableArray([]);

    // Load product areas, create map by ID
    $.getJSON("/api/product_areas", function(data) {
        $.each(data, function(i, productArea) {
            viewModel.productAreas.push(productArea);
            viewModel.productAreaMap[productArea._id] = productArea;
        });
    });

    // Load available clients
    $.getJSON("/api/clients", function(data) {
        selectClient(data[0]);
        $.each(data, function(i, client) {
            client.isSelected = ko.observable(false);
            viewModel.clients.push(client);
        });
    });

    ko.applyBindings(this);
};
var viewModel = new ViewModel();


/**
 * Individual feature request model
 */
var FeatureRequest = function(request, index) {

    /**
     * Methods:
     */
    this.startEditing = function() {
        // Marks the FeatureRequest as being editted, swapping static text
        // for input fields

        this._editing(true);
    };

    this.saveChanges = function() {
        // Ends editting and commits changes to REST API

        this._editing(false);
        this.save();
    };

    this.updatePriority = function(priority) {
        // Commits client_priority changes ONLY to the REST API

        this.client_priority(priority);
        if (this._id()) {
            $.ajax({
                type: "PUT",
                url: "/api/feature_requests/" + this._id(),
                data: ko.toJSON({
                    _id: this._id(),
                    client_priority: priority
                })
            })
        }
    }

    this.save = function() {
        // Commits all changes to the REST API

        if (!this._id()) {
            // Request is new, issue a POST request to create
            var savedRequest = this;
            $.ajax({
                type: "POST",
                url: "/api/feature_requests",
                data: ko.toJSON(this),
                success: function(data, status) {
                    savedRequest._id(data._id);
                }
            })
        }
        else {
            // Issue exists, issue a PUT to update
            $.ajax({
                type: "PUT",
                url: "/api/feature_requests/" + this._id(),
                data: ko.toJSON(this)
            })
        }

        // Ensure priorities are still ordered correctly
        reindexPriorities();
    };

    this.moveUp = function() {
        // Swap with feature request above and autosave priorities

        var previous = viewModel.clientRequests()[this.client_priority() - 2];
        viewModel.clientRequests.remove(
            viewModel.clientRequests()[this.client_priority() - 1]
        );
        previous.updatePriority(this.client_priority());
        this.updatePriority(this.client_priority() - 1);
        viewModel.clientRequests.splice(this.client_priority() - 1, 0, this);
    };

    this.moveDown = function() {
        // Swap with feature below and autosave

        var next = viewModel.clientRequests()[this.client_priority()];
        viewModel.clientRequests.remove(
            viewModel.clientRequests()[this.client_priority() - 1]
        );
        next.updatePriority(this.client_priority());
        this.updatePriority(this.client_priority() + 1);
        viewModel.clientRequests.splice(this.client_priority() -1 , 0, this);
    };

    this.deleteRequest = function() {
        // Remove feature request, issuing a DELETE to the REST API if
        // it exists there

        viewModel.clientRequests.remove(
            viewModel.clientRequests()[this.client_priority() - 1]
        );
        if (this._id()) {
            $.ajax({
                type: "DELETE",
                url: "/api/feature_requests/" + this._id()
            });
        }
        reindexPriorities();
    };


    /**
     * Initialize object:
     */
    for (key in request) {
        this[key] = ko.observable(request[key]);
    }
    this._editing = ko.observable(false);
    this._product_area_name = viewModel.productAreaMap[this.product_area_id()].name;
};


var selectClient = function(client, event) {
    // Select a client and load its feature requests
    viewModel.activeClient(client);

    $.getJSON("/api/feature_requests/" + client._id, function(data) {
        viewModel.clientRequests.removeAll();
        $.each(data, function(i, request) {
            viewModel.clientRequests.push(
                new FeatureRequest(request, i)
            );
        });
    });
};


var reindexPriorities = function() {
    // Walk the requests and ensure priorities match the current order
    $.each(viewModel.clientRequests(), function(i, request) {
        if (this.client_priority() != i + 1) {
            this.updatePriority(i + 1);
        }
    });
};


var newFeatureRequest = function() {
    // Create a new feature request and insert it at the end of the list
    // with the highest priority

    var newRequest = new FeatureRequest({
        _id: null, // will be assigned on save
        title: "New Request",
        description: "",
        target_date: "",
        client_id: viewModel.activeClient()._id,
        client_priority: viewModel.clientRequests().length + 1,
        ticket_url: "",
        "product_area_id": 1
    });
    newRequest._editing(true);
    viewModel.clientRequests.push(newRequest);
};

// Create koFocus binding that's one-way, unlike hasFocus.
// This lets us autofocus the title of an actively editing request
// without linking editing and focus strongly together
ko.bindingHandlers.koFocus = {
    update: function (element, valueAccessor) {
        var value = valueAccessor();
        var $element = $(element);
            if (value()) {
                $element.focus();
            }
    }
};
