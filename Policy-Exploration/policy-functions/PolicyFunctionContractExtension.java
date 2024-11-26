package org.eclipse.edc.sample.extension.policy;

import org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext;
import org.eclipse.edc.policy.engine.spi.PolicyEngine;
import org.eclipse.edc.policy.engine.spi.RuleBindingRegistry;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import static org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext.NEGOTIATION_SCOPE;
import static org.eclipse.edc.jsonld.spi.PropertyAndTypeNames.ODRL_USE_ACTION_ATTRIBUTE;
import static org.eclipse.edc.policy.engine.spi.PolicyEngine.ALL_SCOPES;
import static org.eclipse.edc.spi.constants.CoreConstants.EDC_NAMESPACE;

public class PolicyFunctionsExtension implements ServiceExtension {
    private static final String TIME_CONSTRAINT_KEY = EDC_NAMESPACE + "currentTime";
    
    @Inject
    private RuleBindingRegistry ruleBindingRegistry;
    @Inject
    private PolicyEngine policyEngine;
    
    @Override
    public String name() {
        return "Sample policy functions";
    }
    
    @Override
    public void initialize(ServiceExtensionContext context) {
        var monitor = context.getMonitor();
        
        ruleBindingRegistry.bind(ODRL_USE_ACTION_ATTRIBUTE, ALL_SCOPES);
        ruleBindingRegistry.bind(TIME_CONSTRAINT_KEY, NEGOTIATION_SCOPE);
        policyEngine.registerFunction(ContractNegotiationPolicyContext.class, Permission.class, TIME_CONSTRAINT_KEY, new TimeConstraintFunction(monitor));
    }
}