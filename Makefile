FILES=bgp.py
TEST_FILES=test_bgp.py
ALL_FILES=$(FILES) $(TEST_FILES)

fmt:
	black $(ALL_FILES)
	isort $(ALL_FILES)

test:
	pytest $(TEST_FILES)

clean:
	$(RM) -r .pytest* *cache*

.PHONY: clean
