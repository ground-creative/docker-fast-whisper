 #!/bin/sh

# Run command
if [ "${TEST}" = true ]; then 
	echo "======= Running test command \"tail -f /dev/null\"";
	tail -f /dev/null;
else 
	# Add env vars to command
	COMMAND=$(echo "${COMMAND}" | sed "s/__SERVER_ADDRESS__/${SERVER_ADDRESS}/g; s/__SERVER_PORT__/${SERVER_PORT}/g")
	echo "======= Running command \"${COMMAND}\"";
	eval "${COMMAND}";
fi
