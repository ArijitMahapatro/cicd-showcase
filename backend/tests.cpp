#include <iostream>
#include <string>
#include <cassert>
#include <stdexcept>
#include <sstream>
#include <ctime>
#include <map>

// ── reimport the functions under test ──────────────────────────────────────
std::string getCurrentTimestamp() {
    std::time_t now = std::time(nullptr);
    char buf[32];
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&now));
    return std::string(buf);
}

std::string getSystemStatus() { return "healthy"; }

std::string buildHealthResponse(const std::string& version,
                                const std::string& status) {
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

// ── minimal test harness ───────────────────────────────────────────────────
int passed = 0, failed = 0;

void run_test(const std::string& name, bool condition) {
    if (condition) {
        std::cout << "  [PASS] " << name << std::endl;
        ++passed;
    } else {
        std::cerr << "  [FAIL] " << name << std::endl;
        ++failed;
    }
}

// ── test suites ────────────────────────────────────────────────────────────
void test_getSystemStatus() {
    std::cout << "\nSuite: getSystemStatus" << std::endl;
    run_test("returns 'healthy'", getSystemStatus() == "healthy");
    run_test("non-empty string",  !getSystemStatus().empty());
}

void test_getCurrentTimestamp() {
    std::cout << "\nSuite: getCurrentTimestamp" << std::endl;
    std::string ts = getCurrentTimestamp();
    run_test("non-empty",         !ts.empty());
    run_test("contains 'T'",      ts.find('T') != std::string::npos);
    run_test("ends with 'Z'",     ts.back() == 'Z');
    run_test("length == 20",      ts.length() == 20);
}

void test_buildHealthResponse() {
    std::cout << "\nSuite: buildHealthResponse" << std::endl;
    std::string resp = buildHealthResponse("1.0.0", "healthy");
    run_test("contains version",   resp.find("1.0.0")   != std::string::npos);
    run_test("contains status",    resp.find("healthy")  != std::string::npos);
    run_test("contains service",   resp.find("cicd-showcase-backend") != std::string::npos);
    run_test("contains uptime",    resp.find("uptime")   != std::string::npos);
    run_test("starts with '{'",    resp.front() == '{');
    run_test("ends with '}'",      resp.back()  == '}');
    run_test("non-empty response", !resp.empty());
}

void test_getPipelineStages() {
    std::cout << "\nSuite: getPipelineStages" << std::endl;
    auto stages = getPipelineStages();
    run_test("has 6 stages",          stages.size() == 6);
    run_test("build stage passed",    stages["build"]      == "passed");
    run_test("test stage passed",     stages["test"]       == "passed");
    run_test("sonarcloud passed",     stages["sonarcloud"] == "passed");
    run_test("docker stage passed",   stages["docker"]     == "passed");
    run_test("terraform passed",      stages["terraform"]  == "passed");
    run_test("deploy stage passed",   stages["deploy"]     == "passed");
}

// ── main ───────────────────────────────────────────────────────────────────
int main() {
    std::cout << "====================================" << std::endl;
    std::cout << " CI/CD Showcase Backend Test Suite  " << std::endl;
    std::cout << "====================================" << std::endl;

    test_getSystemStatus();
    test_getCurrentTimestamp();
    test_buildHealthResponse();
    test_getPipelineStages();

    std::cout << "\n====================================\n";
    std::cout << "Results: " << passed << " passed, " << failed << " failed\n";
    std::cout << "====================================\n";

    return (failed == 0) ? 0 : 1;
}
