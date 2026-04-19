#include <iostream>
#include <string>
#include <ctime>
#include <sstream>
#include <map>

// Simple C++ health check service
// Demonstrates: build system, unit tests, compiler/linker in CI

std::string getCurrentTimestamp() {
    std::time_t now = std::time(nullptr);
    char buf[32];
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&now));
    return std::string(buf);
}

std::string getSystemStatus() {
    return "healthy";
}

std::string buildHealthResponse(const std::string& version, const std::string& status) {
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"status\": \"" << status << "\",\n";
    oss << "  \"version\": \"" << version << "\",\n";
    oss << "  \"timestamp\": \"" << getCurrentTimestamp() << "\",\n";
    oss << "  \"service\": \"cicd-showcase-backend\",\n";
    oss << "  \"uptime\": \"running\"\n";
    oss << "}";
    return oss.str();
}

std::map<std::string, std::string> getPipelineStages() {
    std::map<std::string, std::string> stages;
    stages["build"]     = "passed";
    stages["test"]      = "passed";
    stages["sonarcloud"]= "passed";
    stages["docker"]    = "passed";
    stages["terraform"] = "passed";
    stages["deploy"]    = "passed";
    return stages;
}

int main() {
    const std::string VERSION = "1.0.0";

    std::cout << "=== CI/CD Showcase Backend Service ===" << std::endl;
    std::cout << "Version: " << VERSION << std::endl;
    std::cout << "Timestamp: " << getCurrentTimestamp() << std::endl;
    std::cout << std::endl;

    std::string healthJson = buildHealthResponse(VERSION, getSystemStatus());
    std::cout << "Health Check Response:" << std::endl;
    std::cout << healthJson << std::endl;
    std::cout << std::endl;

    std::cout << "Pipeline Stage Status:" << std::endl;
    auto stages = getPipelineStages();
    for (const auto& stage : stages) {
        std::cout << "  [" << stage.second << "] " << stage.first << std::endl;
    }

    std::cout << std::endl;
    std::cout << "Backend service initialized successfully." << std::endl;
    return 0;
}
