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
 * The {{FLAG_BYTES}} placeholder is replaced at build time with C
 * source like:  s[0]='C'; s[1]='T'; ... etc.
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

/* Reconstruct the diagnostic signature in a local stack buffer.
 * Each byte is assigned individually so the resulting string
 * never appears in any data section. */
static int run_signature_check(void) {
    /* Reserve enough space for the longest plausible flag.
     * Build will populate the assignments. */
    volatile char sig[256] = {0};

    /* {{FLAG_BYTES}} */

    /* "Use" the constructed buffer so the optimizer doesn't
     * eliminate the assignments. We compute a trivial checksum
     * and discard it - the bytes still get written. */
    volatile unsigned int checksum = 0;
    for (int i = 0; i < (int)sizeof(sig); i++) {
        checksum += (unsigned char)sig[i];
    }
    return (checksum != 0) ? 0 : 1;
}

int main(int argc, char** argv) {
    printf("=== Acme Corp Diagnostic Suite v1.4.0 ===\n");
    printf("%s\n", MSG_START);
    printf("%s\n", MSG_CPU);
    printf("%s\n", MSG_MEM);
    printf("%s\n", MSG_DISK);
    printf("%s\n", MSG_NET);

    /* Run the internal signature check (constructs the stacked string).
     * We don't print the result - this is intentional. */
    int sig_status = run_signature_check();
    (void)sig_status;

    printf("%s\n", MSG_DONE);
    printf("%s\n", MSG_LOG);
    printf("For support, visit %s\n", SUPPORT_URL);
    return 0;
}
