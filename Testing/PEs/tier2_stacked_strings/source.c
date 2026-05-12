/*
 * SystemDiagnostic.exe - Tier 2 PE CTF challenge source
 *
 * Looks like a system diagnostic utility. The flag is constructed
 * at runtime via byte-by-byte stack assignments (a "stacked string"),
 * so it never appears contiguously in any data section.
 *
 * `strings` cannot find this flag. The intended solving tool is
 * FLOSS (https://github.com/mandiant/flare-floss), which emulates
 * functions to recover stack-constructed strings.
 *
 * The placeholder in run_signature_check below is replaced at build
 * time by build.py with C source like:
 *   sig[0] = 0x43;  sig[1] = 0x54;  ...
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Decoy strings - look like real diagnostic logic.
 * Marked 'used' so optimizer keeps them in .rdata for the strings dump. */
__attribute__((used)) static const char* VENDOR = "Acme Corporation - Diagnostic Suite v1.4.0";
__attribute__((used)) static const char* MSG_START = "Starting system diagnostic...";
__attribute__((used)) static const char* MSG_CPU = "Checking CPU... OK";
__attribute__((used)) static const char* MSG_MEM = "Checking memory... OK";
__attribute__((used)) static const char* MSG_DISK = "Checking disk... OK";
__attribute__((used)) static const char* MSG_NET = "Checking network... OK";
__attribute__((used)) static const char* MSG_DONE = "All checks passed.";
__attribute__((used)) static const char* MSG_LOG = "Log written to: C:\\ProgramData\\AcmeCorp\\diag.log";
__attribute__((used)) static const char* SUPPORT_URL = "https://support.acme-corp.local/diagnostics";

__attribute__((noinline))
static unsigned int run_signature_check(void) {
    char sig[256] = {0};

    /* {{FLAG_BYTES}} */

    unsigned int checksum = 0;
    for (int i = 0; i < 256; i++) {
        checksum = (checksum * 33) + (unsigned char)sig[i];
    }

    __asm__ volatile ("" : : "r"(sig) : "memory");

    return checksum;
}

int main(int argc, char** argv) {
    printf("=== Acme Corp Diagnostic Suite v1.4.0 ===\n");
    printf("%s\n", MSG_START);
    printf("%s\n", MSG_CPU);
    printf("%s\n", MSG_MEM);
    printf("%s\n", MSG_DISK);
    printf("%s\n", MSG_NET);

    unsigned int sig_status = run_signature_check();

    printf("%s\n", MSG_DONE);
    printf("%s\n", MSG_LOG);
    printf("For support, visit %s\n", SUPPORT_URL);

    return (int)(sig_status & 0xFF);
}
