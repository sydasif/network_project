# Django + Nornir Refactoring - Plan for Nornir-Centric Architecture

## 🎯 **Corrected Understanding**

- **Primary Library**: Nornir (inventory management, task orchestration, result aggregation)
- **Nornir Plugins**: Netmiko, NAPALM, Scrapli (as connection/task plugins within Nornir)
- **Architecture**: Single Nornir executor with multiple plugin backends

---

## **Revised Task Prompts - Nornir-Centric Approach**

## **Phase 1: Nornir Foundation & Plugin Management**

### **Task 1 Prompt: Create Nornir Base Structure**

```bash
Create a Nornir-centric base structure for Django network automation that uses Nornir as the main orchestration layer with Netmiko, NAPALM, and Scrapli as plugins.

Requirements:
1. Create `core/nornir/` directory structure:
   - `nornir_manager.py` - Main Nornir orchestration class
   - `inventory_builder.py` - Django models to Nornir inventory conversion
   - `plugin_manager.py` - Manage Nornir plugins (netmiko, napalm, scrapli)
   - `result_processor.py` - Standardize Nornir results across plugins

2. Implement `NornirManager` class with:
   - `initialize_nornir(inventory_source)` - Setup Nornir with Django inventory
   - `get_connection_plugin(device)` - Select appropriate plugin (netmiko/napalm/scrapli)
   - `execute_task(task_name, devices, **kwargs)` - Run tasks via appropriate plugin
   - `close_connections()` - Cleanup all connections

3. Plugin selection logic based on:
   - Device platform (cisco_ios -> netmiko, ios -> napalm, etc.)
   - Task type (config -> napalm, show commands -> netmiko)
   - User preference or device-specific settings

4. Result standardization:
   - Unified result format regardless of underlying plugin
   - Error handling across different plugin types
   - Progress tracking and logging

Focus on Nornir as the orchestration layer, not multiple separate executors.
```

### **Task 2 Prompt: Django to Nornir Inventory Integration**

```bash
Create seamless integration between Django Device models and Nornir inventory system with support for dynamic inventory updates.

Requirements:
1. Update `core/models.py` with Nornir-specific fields:
   - Device model with nornir_plugin field (netmiko, napalm, scrapli)
   - Platform field for plugin selection logic
   - Connection parameters as JSONField
   - Group assignments for Nornir groups

2. Create `core/nornir/inventory_builder.py`:
   - `DjangoInventory` class inheriting from Nornir's InventoryPluginRegister
   - `load()` method to convert Django devices to Nornir inventory
   - Dynamic group creation based on Django device groups
   - Host data transformation for each plugin type

3. Implement inventory features:
   - Real-time inventory updates when Django models change
   - Filtering devices for specific Nornir operations
   - Credential management integration
   - Connection parameter formatting per plugin

4. Plugin-specific inventory formatting:
   - Netmiko: device_type, host, username, password mapping
   - NAPALM: driver, hostname, username, password mapping
   - Scrapli: platform, host, auth_username, auth_password mapping

Include Django signals to update Nornir inventory when device models change.
```

### **Task 3 Prompt: Nornir Plugin Strategy Implementation**

```bash
Implement intelligent plugin selection strategy within Nornir for choosing between Netmiko, NAPALM, and Scrapli based on device and task requirements.

Requirements:
1. Create `core/nornir/plugin_manager.py`:
   - `PluginSelector` class for intelligent plugin selection
   - Platform-to-plugin mapping configuration
   - Task-type-to-plugin optimization
   - Fallback mechanisms when primary plugin fails

2. Plugin selection logic:
   - **Platform-based**: ios/ios-xe -> netmiko, junos -> napalm, eos -> scrapli
   - **Task-based**: configuration tasks -> napalm, show commands -> netmiko
   - **Performance-based**: fastest plugin for specific operations
   - **Feature-based**: specific plugin features (NAPALM config replace, etc.)

3. Create configuration system:
   - YAML/JSON config files for plugin preferences
   - Per-device plugin overrides
   - Task-specific plugin requirements
   - Global defaults with device exceptions

4. Implement plugin validation:
   - Check plugin availability and installation
   - Validate plugin compatibility with device platform
   - Test plugin connectivity before task execution
   - Handle plugin-specific errors gracefully

Include comprehensive error handling and plugin availability checking.
```

## **Phase 2: Nornir Task Framework**

### **Task 4 Prompt: Nornir Task Abstraction Layer**

```
Create a task abstraction layer that leverages Nornir's task system while providing a unified interface for different plugin operations.

Requirements:
1. Create `core/tasks/nornir_tasks/` with plugin-agnostic task wrappers:
   - `configuration_tasks.py` - get_config, set_config, backup_config
   - `information_tasks.py` - show commands, device facts, interface status
   - `discovery_tasks.py` - CDP/LLDP, routing tables, ARP tables
   - `maintenance_tasks.py` - ping tests, connectivity checks

2. Each task module should:
   - Use Nornir's task decoration (@task)
   - Automatically select appropriate plugin (netmiko/napalm/scrapli)
   - Handle plugin-specific parameters and results
   - Provide consistent error handling

3. Create `core/tasks/task_dispatcher.py`:
   - `TaskDispatcher` class that wraps Nornir.run()
   - Intelligent task routing to appropriate plugins
   - Result aggregation and standardization
   - Progress tracking and logging

4. Task execution features:
   - Parallel execution across devices via Nornir
   - Plugin fallback (try netmiko, fallback to napalm)
   - Task result caching and storage
   - Detailed execution logging

Focus on leveraging Nornir's built-in concurrency and result aggregation.
```

### **Task 5 Prompt: Plugin-Specific Task Implementation**

```
Implement specific Nornir tasks that utilize Netmiko, NAPALM, and Scrapli plugins effectively for different network operations.

Requirements:
1. Create Netmiko-based tasks in `core/tasks/plugins/netmiko_tasks.py`:
   - `netmiko_send_command()` - for show commands
   - `netmiko_send_config()` - for configuration changes
   - `netmiko_file_transfer()` - for file operations
   - Integration with nornir_netmiko plugin

2. Create NAPALM-based tasks in `core/tasks/plugins/napalm_tasks.py`:
   - `napalm_get_facts()` - device information gathering
   - `napalm_get_config()` - configuration retrieval
   - `napalm_config_replace()` - full configuration replacement
   - `napalm_config_merge()` - configuration merging
   - Integration with nornir_napalm plugin

3. Create Scrapli-based tasks in `core/tasks/plugins/scrapli_tasks.py`:
   - `scrapli_send_command()` - optimized command execution
   - `scrapli_send_configs()` - configuration deployment
   - `scrapli_get_prompt()` - device state checking
   - Integration with nornir_scrapli plugin

4. Task orchestration:
   - Plugin selection logic within each task
   - Error handling specific to each plugin
   - Result format standardization
   - Performance optimization per plugin

Each task should be a proper Nornir task that can be used with nr.run().
```

## **Phase 3: Enhanced Nornir Integration**

### **Task 6 Prompt: Advanced Nornir Result Processing**

```
Create advanced result processing system that standardizes and enhances Nornir results from different plugins.

Requirements:
1. Create `core/nornir/result_processor.py`:
   - `NornirResultProcessor` class for result standardization
   - Plugin-specific result parsing and formatting
   - Error extraction and categorization
   - Success/failure determination across plugins

2. Result standardization features:
   - Convert all plugin results to common format
   - Extract structured data from text output
   - Normalize error messages across plugins
   - Timestamp and metadata addition

3. Create `core/nornir/parsers/` for output parsing:
   - `textfsm_parser.py` - TextFSM integration for structured data
   - `regex_parser.py` - Custom regex parsing patterns
   - `json_extractor.py` - Extract JSON from mixed output
   - Platform-specific parsing rules

4. Result storage and retrieval:
   - Save results to Django models
   - Result querying and filtering
   - Historical result comparison
   - Export capabilities (JSON, CSV, Excel)

Focus on leveraging Nornir's MultiResult and Result objects effectively.
```

### **Task 7 Prompt: Nornir Configuration Management**

```
Implement comprehensive Nornir configuration management for Django integration with proper initialization and cleanup.

Requirements:
1. Create `core/nornir/config_manager.py`:
   - `NornirConfig` class for managing Nornir settings
   - Dynamic configuration based on Django settings
   - Plugin configuration management
   - Logging and debugging configuration

2. Nornir initialization:
   - Custom InitNornir() wrapper for Django integration
   - Inventory plugin registration (Django inventory)
   - Connection plugin configuration (netmiko, napalm, scrapli)
   - Transform function registration

3. Create `core/nornir/connection_manager.py`:
   - Connection pooling for Nornir connections
   - Connection lifecycle management
   - Plugin-specific connection handling
   - Connection health monitoring

4. Configuration features:
   - Environment-based configuration (dev, prod)
   - Plugin availability detection
   - Performance tuning parameters
   - Debug and logging levels

Include proper Nornir cleanup and resource management.
```

## **Phase 4: Django Integration Layer**

### **Task 8 Prompt: Django Views for Nornir Operations**

```
Create Django views that provide web interface for Nornir-based network operations with real-time feedback.

Requirements:
1. Create `core/views/nornir_views.py`:
   - `DeviceListView` with Nornir inventory integration
   - `TaskExecutionView` for running Nornir tasks
   - `ResultDisplayView` for showing task results
   - `InventoryManagementView` for device management

2. Task execution interface:
   - Form-based task parameter input
   - Device selection with filtering
   - Plugin selection override options
   - Real-time execution progress

3. Create `core/forms/nornir_forms.py`:
   - `TaskExecutionForm` with dynamic field generation
   - `DeviceSelectionForm` with inventory integration
   - `PluginConfigurationForm` for plugin settings
   - Validation based on selected plugins and devices

4. AJAX integration:
   - Asynchronous task execution
   - Progress updates during execution
   - Real-time result streaming
   - Error handling and user feedback

Include proper error handling and user experience considerations.
```

### **Task 9 Prompt: Celery Integration for Async Nornir Tasks**

```
Integrate Celery with Nornir for asynchronous task execution with proper progress tracking and result storage.

Requirements:
1. Create `core/tasks/celery_tasks.py`:
   - `execute_nornir_task.delay()` Celery task
   - Progress tracking with Celery result backend
   - Task cancellation support
   - Result storage in Django models

2. Async execution features:
   - Long-running task support
   - Task queuing and prioritization
   - Concurrent task execution limits
   - Task retry logic with exponential backoff

3. Create `core/utils/task_tracker.py`:
   - Task status tracking (pending, running, completed, failed)
   - Progress percentage calculation
   - Real-time updates via WebSocket or polling
   - Task result notification system

4. Integration points:
   - Django admin integration for task monitoring
   - API endpoints for task status queries
   - WebSocket updates for real-time progress
   - Email notifications for task completion

Focus on proper Celery-Nornir integration and resource management.
```

## **Phase 5: API and Advanced Features**

### **Task 10 Prompt: REST API for Nornir Operations**

```
Create comprehensive REST API for Nornir-based network automation with full operation support.

Requirements:
1. Create `core/api/nornir_api.py` with DRF:
   - `/api/devices/` - device management with Nornir inventory sync
   - `/api/tasks/execute/` - trigger Nornir task execution
   - `/api/tasks/status/{task_id}/` - check task execution status
   - `/api/results/` - query and export task results

2. API features:
   - Device filtering for task execution
   - Plugin selection via API parameters
   - Bulk operations support
   - Task scheduling and queuing

3. Create `core/serializers/nornir_serializers.py`:
   - Device serializer with Nornir inventory fields
   - Task execution serializer with plugin options
   - Result serializer with standardized output
   - Validation for plugin compatibility

4. Advanced API features:
   - OpenAPI documentation with plugin details
   - Rate limiting for resource-intensive operations
   - API authentication and authorization
   - Webhook notifications for task completion

Include comprehensive API documentation and testing.
```

### **Task 11 Prompt: Monitoring and Logging for Nornir Operations**

```
Implement comprehensive monitoring, logging, and alerting specifically for Nornir-based operations.

Requirements:
1. Create `core/monitoring/nornir_monitor.py`:
   - Task execution metrics (duration, success rate, plugin usage)
   - Device connectivity monitoring via Nornir
   - Plugin performance comparison
   - Resource usage tracking

2. Nornir-specific logging:
   - Structured logging for all Nornir operations
   - Plugin-specific log formatting
   - Task correlation across multiple devices
   - Error categorization by plugin type

3. Create `core/monitoring/health_checks.py`:
   - Nornir initialization health check
   - Plugin availability monitoring
   - Device reachability checks via Nornir
   - Inventory synchronization status

4. Alerting system:
   - Task failure notifications
   - Plugin connectivity issues
   - Performance degradation alerts
   - Inventory inconsistency warnings

Include dashboard integration and reporting capabilities.
```

---

## **Key Corrections Made:**

### ✅ **Aligned with Your Requirements:**
1. **Nornir as Primary**: All tasks now focus on Nornir as the main orchestration layer
2. **Plugins, Not Separate Executors**: Netmiko, NAPALM, Scrapli are treated as Nornir plugins
3. **Single Integration Point**: One Nornir manager instead of multiple executor factories
4. **Plugin Selection Logic**: Intelligent selection within Nornir ecosystem

### ✅ **Simplified Architecture:**
- Removed unnecessary executor abstractions
- Focused on Nornir's built-in inventory and task systems
- Leveraged Nornir's native concurrency and result aggregation
- Used Nornir's plugin ecosystem properly

### ✅ **Nornir-Centric Features:**
- Django to Nornir inventory integration
- Proper use of Nornir tasks and results
- Plugin selection within Nornir framework
- Leveraging Nornir's strengths (inventory, concurrency, results)

This revised plan is much more aligned with your actual requirements of using Nornir as the main library with other libraries as plugins underneath it.