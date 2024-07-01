# SecreTUM

## About

This repository contains the code for the SecreTUM project.

## Structure

```mermaid
flowchart TD
    subgraph Raspberry Pi
        direction TB
        subgraph "Local Network (Docker containers, IO managed by Traefik)"
            subgraph Docker
                Traefik["Traefik<br>(reverse proxy)"]
                Redis["Redis Database<br>(in-memory database<br>for measurements)"]
                Grafana["Grafana Dashboard<br>(displays measurements<br>and telemetry)"]
                DataProcessing["Data Processing Routine<br>(Python script)"]
            end

            MeasurementService["Measurement Service<br>(C/Python program)"]
        end
        subgraph IO
            GPIO
            Display["Local Display"]
            WiFi["WiFi AP"]
            DashboardEndpoint["Grafana Dashboard Endpoint<br>http://secretum.local"]
        end
        Browser["Local Browser"]
    end
    subgraph Peripheral Devices
        BufferReservoir["Buffer Reservoir"]
        DiscardReservoir["Discard Reservoir"]
        Needle["Test Needle"]
        OpticalSensor["Optical Sensor"]
        OurSensor["Our Sensor"]
        BufferPump["Buffer Pump"]
        TestPump["Test Pump"]

    end
    subgraph Organizers
        TestReservoir["Test Reservoir"]
        Laptop["Laptop with a browser"]
    end

    MeasurementService -->|Writes measurements to| Redis
    MeasurementService -->|Reads sensor data and telemetry<br>Writes pump contol data| GPIO
    MeasurementService -->|Writes data to| Redis
    DataProcessing -->|Reads measurements from| Redis
    DataProcessing -->|Writes recognition data to| Redis
    Grafana -->|Reads data from| Redis
    DashboardEndpoint -->|Managed by| Traefik
    Browser -->|Accesses data via| DashboardEndpoint
    Display -->|Shows data from| Browser
    GPIO -->|Controls| TestPump
    GPIO -->|Controls| BufferPump
    OurSensor -->|Sends data to| GPIO
    OpticalSensor -->|Sends data to| GPIO
    BufferReservoir -->|Supplies liquid to| BufferPump
    BufferPump -->|Pushes liquid through| OurSensor
    OurSensor -->|Discards liquid to| DiscardReservoir
    Needle -->|Supplies liquid to| TestPump
    TestPump -->|Pushes test liquid through| OurSensor
    Needle -->|Triggers| OpticalSensor
    TestReservoir -->|Fills| Needle
    Laptop -->|Accesses dashboard via| DashboardEndpoint
    Laptop -->|Connects to| WiFi
```

## TODO

### Controller

- [ ] Check the logic of the controller
- [ ] Test the state machine using the API
- [ ] test the state machine using the Measurement Service

### GPIO

- [ ] Check the plausibility of the GPIO interface
- [ ] Test writing back to the GPIO interface (channel updates)
- [ ] Test Raspberry Pi 5 compatibility

### Measurement Service

- [ ] Figure out how to properly store time series data
- [ ] Figure out required discretization rate

### Data Processing

- [ ] Figure out the shape of the data
- [ ] Figure out how to properly process the data
- [ ] Make sure the data is stored in the Redis database

### API

- [ ] Implement the GPIO API
- [ ] Implement the Measurement API
- [ ] Implement the State Machine API

### Grafana

- [ ] Make grafana load the dashboard from the file system
- [ ] Add sensor data to the dashboard
- [ ] Add state machine data to the dashboard
- [ ] Add pump controls to the dashboard
- [ ] Add recognition data to the dashboard
- [ ] Add mock GPIO controls to the dashboard
- [ ] Measure the total system latency

### Hardware

- [ ] Test the optical sensor
- [ ] Test the Raspberry Pi 5 GPIO interface
- [ ] Assemble the hardware

### Deployment

- [ ] Add a Dockerfile for the Measurement Service
- [ ] Make sure Grafana can be accessed via the local network
- [ ] Make sure API calls do not fail on the local network

