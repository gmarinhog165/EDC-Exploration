package org.eclipse.edc.sample.extension.policy;

import org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext;
import org.eclipse.edc.policy.engine.spi.AtomicConstraintRuleFunction;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.spi.monitor.Monitor;

import org.eclipse.edc.participant.spi.ParticipantAgentPolicyContext;

import java.util.Collection;
import java.util.Objects;

import java.time.Instant;
import java.time.format.DateTimeParseException;

import static java.lang.String.format;

public class TimeConstraintFunction implements AtomicConstraintRuleFunction<Permission, ParticipantAgentPolicyContext> {
    
    private final Monitor monitor;
    
    public TimeConstraintFunction(Monitor monitor) {
        this.monitor = monitor;
    }
    
    @Override
    public boolean evaluate(Operator operator, Object rightValue, Permission rule, ParticipantAgentPolicyContext context) {
        try {
            Instant now = Instant.now();

            monitor.info(format("TimeConstraintFunction: Current time is %s", now));

            if (!(rightValue instanceof String)) {
                monitor.warning("TimeConstraintFunction: Right value is not a valid ISO-8601 datetime string.");
                return false;
            }

            Instant expectedTime = Instant.parse((String) rightValue);

            monitor.info(format(
                "TimeConstraintFunction: Evaluating constraint with operator='%s', now='%s', expectedTime='%s'",
                operator, now, expectedTime
            ));

            boolean result = switch (operator) {
                case GEQ -> {
                    boolean isSatisfied = now.equals(expectedTime) || now.isAfter(expectedTime);
                    monitor.info(format("TimeConstraintFunction: GEQ evaluation result: %s", isSatisfied));
                    yield isSatisfied;
                }
                case LEQ -> {
                    boolean isSatisfied = now.equals(expectedTime) || now.isBefore(expectedTime);
                    monitor.info(format("TimeConstraintFunction: LEQ evaluation result: %s", isSatisfied));
                    yield isSatisfied;
                }
                default -> {
                    monitor.warning(format("TimeConstraintFunction: Unsupported operator '%s'", operator));
                    yield false;
                }
            };

            monitor.info(format("TimeConstraintFunction: Final evaluation result: %s", result));
            return result;

        } catch (DateTimeParseException e) {
            monitor.warning(format("TimeConstraintFunction: Invalid date format for right value: '%s'", rightValue));
            return false;
        }
    }
}