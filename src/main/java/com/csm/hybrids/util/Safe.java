package com.csm.hybrids.util;

import com.csm.hybrids.CsmMod;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * A move, summon or effect that breaks must not take the whole game down with it. Code run through here that throws
 * is stopped instead: the error is logged (once per thing that broke, with its stack trace, so it can be reported and
 * fixed) and the caller cleans up - the move is cancelled, the summon vanishes, the model is not drawn this frame.
 */
public final class Safe {
    private static final Set<String> REPORTED = ConcurrentHashMap.newKeySet();
    private static final AtomicInteger ERRORS = new AtomicInteger();

    /** @return false if {@code action} threw (and was stopped). */
    public static boolean run(String what, Runnable action) {
        try {
            action.run();
            return true;
        } catch (RuntimeException | LinkageError e) {
            report(what, e);
            return false;
        }
    }

    public static void report(String what, Throwable e) {
        ERRORS.incrementAndGet();
        if (REPORTED.add(what)) {
            CsmMod.LOGGER.error("[csm] {} broke and was stopped so the game can go on - please report this log", what, e);
        }
    }

    /** How many times something was stopped (the smoke test fails on any). */
    public static int errors() {
        return ERRORS.get();
    }

    public static List<String> reported() {
        return new ArrayList<>(REPORTED);
    }

    private Safe() {
    }
}
