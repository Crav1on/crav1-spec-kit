**What it is.** Private Link gives an Azure service a private address inside your own virtual network, so traffic to it never crosses the public internet.

**How it works.** You create a private endpoint in a subnet. It gets a private IP address that maps to one instance of a service, such as one storage account. Private DNS then makes the service's usual name resolve to that address from inside the network.

**Where it shows up.** The specs do not mention Private Link. Nothing in the specs, plans, tasks, design topics or ADRs names it, so there is no spec link to give.

**Why it is used.** In general it is used when a service must not be reachable from the internet, or when a policy says data may only travel on private networks. Whether that applies here is not written down.

**Main tradeoff.** Each endpoint and its DNS zone is one more piece to set up per environment, and a DNS mistake breaks access in ways that are hard to see.

**One alternative.** Service endpoints keep the public address but limit access to chosen subnets. They are simpler and free, and they win when a private address is not required.

Run next:
Private Link is not in the specs, so the answer above is general.

Ask for research on Private Link:
`/crav1-show-or-ask-open-questions ask research private-link`
