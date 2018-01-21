ENTITY test IS
  PORT(
		clk	:	IN	STD_LOGIC;
		reset	:	IN	STD_LOGIC;
		input	:	IN	STD_LOGIC_VECTOR(2 downto 0);
		output	:	OUT	STD_LOGIC_VECTOR(3 downto 0));
END test;
ARCHITECTURE a OF test IS
   TYPE STATE_TYPE IS (s0, s1, s2, s3);
   SIGNAL state : STATE_TYPE;
BEGIN
  PROCESS (clk, reset)
  BEGIN
    IF reset = '1' THEN
      state <= s0;
    ELSIF (clk'EVENT AND clk = '1') THEN
      CASE state IS
				WHEN s0=>
					IF input = "1" THEN
						state <= s1;
					ELSE
						state <= s0;
					END IF;
				WHEN s1=>
					IF input = "2" THEN
						state <= s2;
					ELSE
						state <= s0;
					END IF;
				WHEN s2=>
					IF input = "3" THEN
						state <= s2;
					ELSIF input = "4" THEN
						state <= s3;
					ELSE
						state <= s0;
					END IF;
				WHEN s3=>
					state <= s0;
      END CASE;
    END IF;
  END PROCESS;

  PROCESS (state)
  BEGIN
    CASE state IS
				WHEN s1=>
					output <= "8";
				WHEN s3=>
					output <= "1";
    END CASE;
  END PROCESS;
END a;
